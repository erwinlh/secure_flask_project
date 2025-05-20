 select * from (SELECT 
        
        
        DATE_FORMAT(`fi`.`fecha`, '%Y-%m-%d') AS `Fecha_fi`,
        
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))
            THEN
                (CASE
                    WHEN (`fi`.`tipo` = 33) THEN 1110401021
                    WHEN (`fi`.`tipo` = 110) THEN 1110401022
                    WHEN (`fi`.`tipo` = 39) THEN 1110401023
                    ELSE NULL
                END)
            ELSE 2120404002
        END) AS `cuenta`,
        CONCAT('Dunas Caja del ',
                DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d')) AS `comentario`,
        CONCAT(`aq`.`confirmation_no`,
                ' ',
                `aq`.`pname`,
                ' RM',
                `aq`.`room` ) AS `glosa`,
        (CASE
            WHEN (`aq`.`amt` < 0) THEN (`aq`.`amt` * -(1))
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN (`aq`.`amt` > 0) THEN `aq`.`amt`
            ELSE 0
        END) AS `haberMonedaPrincipal`,


        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut`, '')
            ELSE ''
        END) AS `codigoDeFicha`,
        '' AS `cancelarDocumento`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))
            THEN
                (CASE
                    WHEN (`fi`.`tipo` = 39) THEN 'BEAV'
                    WHEN (`fi`.`tipo` = 33) THEN 'FEAV'
                    WHEN (`fi`.`tipo` = 61) THEN 'NCAV'
                    WHEN (`fi`.`tipo` = 110) THEN 'EEAV'
                    WHEN (`fi`.`tipo` = 112) THEN 'NCEV'
                    ELSE ''
                END)
            ELSE ''
        END) AS `tipoDeDocumento`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`folio`, 0)
            ELSE ''
        END) AS `numeroDeDocumento`,
       
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))
            THEN
                COALESCE(DATE_FORMAT((`fi`.`fecha` + INTERVAL 30 DAY),
                                '%Y-%m-%d'),
                        '')
            ELSE ''
        END) AS `vencimientoDeDocto`,

        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut`, '')
            ELSE ''
        END) AS `codigoLegal`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`aq`.`pname`, '')
            ELSE ''
        END) AS `nombre`,

        '' AS `fecha_aq`
    FROM
        (`dunasdb`.`arqueo` `aq`
        right JOIN `dunasdb`.`fiscales` `fi` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`)))
            and date(fi.fecha) > date(aq.trx_date)
            and fi.total = aq.amt
            )
            
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003)) 
    UNION ALL SELECT 
       
        
        DATE_FORMAT(`fi`.`fecha`, '%Y-%m-%d') AS `Fecha`,
        
        (2120404002) AS `cuenta`,
        CONCAT('Dunas Caja del ',
                DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d')) AS `comentario`,
        CONCAT(`aq`.`confirmation_no`,
                ' ',
                `aq`.`pname`,
                ' RM',
                `aq`.`room`, ' ', aq.remark ,aq.reference) AS `glosa`,
        (CASE
            WHEN (`aq`.`amt` > 0) THEN `aq`.`amt`
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN (`aq`.`amt` < 0) THEN (`aq`.`amt` * -(1))
            ELSE 0
        END) AS `haberMonedaPrincipal`,
        
        '' AS `codigoDeFicha`,
        '' AS `cancelarDocumento`,
        '' AS `tipoDeDocumento`,
        '' AS `numeroDeDocumento`,
        
        '' AS `vencimientoDeDocto`,
       

        '' AS `codigoLegal`,
        '' AS `nombre`,

        COALESCE(CAST(`aq`.`trx_date` AS DATE), '') AS `fecha_aq`
    FROM
        (`dunasdb`.`arqueo` `aq`
        right JOIN `dunasdb`.`fiscales` `fi` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`)))
            and fi.total = aq.amt
            )
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003)
            and date(fi.fecha) > date(aq.trx_date)
            )
            
            ) as q2 
            
where date(q2.fecha_fi) = '2025-03-01' 

order by q2.glosa asc