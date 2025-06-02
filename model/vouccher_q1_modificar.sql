select * from (SELECT 
        DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d') AS `Fecha`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
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
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
            THEN
                CONCAT('i   ',
                        (CASE
                            WHEN (`fi`.`rut` <> `fi`.`rut_defontana`) THEN 'Rut != '
                            ELSE ''
                        END),
                        `aq`.`confirmation_no`,
                        ' ',
                        `aq`.`pname`,
                        ' RM',
                        `aq`.`room`,
                        '.')
            ELSE CONCAT('i   ',
                    `aq`.`confirmation_no`,
                    ' ',
                    `aq`.`pname`,
                    ' RM',
                    `aq`.`room`)
        END) AS `glosa`,
        (CASE
            WHEN (`fi`.`total` < 0) THEN (`fi`.`total` * -(1))
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
            THEN
                (CASE
                    WHEN
                        (`fi`.`tipo` = 33)
                    THEN
                        (CASE
                            WHEN (`fi`.`total` > 0) THEN `fi`.`total`
                            ELSE 0
                        END)
                    WHEN
                        (`fi`.`tipo` = 110)
                    THEN
                        (CASE
                            WHEN (`fi`.`total` > 0) THEN `fi`.`total`
                            ELSE 0
                        END)
                    WHEN
                        (`fi`.`tipo` = 39)
                    THEN
                        (CASE
                            WHEN (`fi`.`total` > 0) THEN `fi`.`total`
                            ELSE 0
                        END)
                    ELSE NULL
                END)
            ELSE (CASE
                WHEN (`aq`.`amt` > 0) THEN `aq`.`amt`
                ELSE 0
            END)
        END) AS `haberMonedaPrincipal`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut_defontana`, '')
            ELSE ''
        END) AS `codigoDeFicha`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
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
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`folio`, 0)
            ELSE 0
        END) AS `numeroDeDocumento`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
            THEN
                COALESCE(DATE_FORMAT((`fi`.`fecha` + INTERVAL 30 DAY),
                                '%Y-%m-%d'),
                        '')
            ELSE ''
        END) AS `vencimientoDeDocto`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut_defontana`, '')
            ELSE ''
        END) AS `codigoLegal`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`aq`.`pname`, '')
            ELSE ''
        END) AS `nombre`, aq.trx_date as trx_Date
    FROM
        (`dunasdb`.`arqueo` `aq`
        left JOIN `dunasdb`.`fiscales` `fi` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`) 
			-- and fi.fecha > aq.trx_date
            ))
            )
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003)) 
            -- and fi.tipo is null
            
            ) as i where i.fecha = '2025-03-05'