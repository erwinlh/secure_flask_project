SELECT 
        
        DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d') AS `Fecha`,
        '' AS `No_Linea`,
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
        CONCAT(`aq`.`confirmation_no`,
                ' ',
                `aq`.`pname`,
                ' RM',
                `aq`.`room`) AS `glosa`,
        (CASE
            WHEN (`aq`.`amt` < 0) THEN (`aq`.`amt` * -(1))
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN (`aq`.`amt` > 0) THEN `aq`.`amt`
            ELSE 0
        END) AS `haberMonedaPrincipal`,
        '' AS `debeMonedaSecundaria`,
        '' AS `haberMonedaSecundaria`,
        '' AS `tasaCambio`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut`, '')
            ELSE ''
        END) AS `codigoDeFicha`,
        '' AS `cancelarDocumento`,
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
        '' AS `serieDeDocumento`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
            THEN
                COALESCE(DATE_FORMAT((`fi`.`fecha` + INTERVAL 30 DAY),
                                '%Y-%m-%d'),
                        '')
            ELSE ''
        END) AS `vencimientoDeDocto`,
        '' AS `CentroDeNegocios`,
        '' AS `Clasificador1`,
        '' AS `Clasificador2`,
        '' AS `MonedaReferencia`,
        '' AS `TasaReferencia`,
        '' AS `TipoDeMovimiento`,
        '' AS `NumeroDeMovimiento`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut`, '')
            ELSE ''
        END) AS `codigoLegal`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`aq`.`pname`, '')
            ELSE ''
        END) AS `nombre`,
        '.' AS `giro`,
        '.' AS `direccion`,
        '.' AS `ciudad`,
        '' AS `rubro`,
        COALESCE(CAST(`fi`.`fecha` AS DATE), '') AS `fecha_`
    FROM
        (`dunasdb`.`arqueo` `aq`
        LEFT JOIN `dunasdb`.`fiscales` `fi` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`))))
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003)) 
    UNION ALL SELECT 
        'A' AS `Numero`,
        'TRASPASO' AS `TipoComprobante`,
        '' AS `MonedaComprobante`,
        DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d') AS `Fecha`,
        '' AS `No_Linea`,
        (CASE
            WHEN (`aq`.`trx_code` = 9000) THEN 1110101001
            WHEN (`aq`.`trx_code` = 9004) THEN 1110402108
            WHEN (`aq`.`trx_code` = 9005) THEN 1110402102
            WHEN (`aq`.`trx_code` = 9006) THEN 1110402106
            WHEN (`aq`.`trx_code` = 9010) THEN 1110402101
            WHEN (`aq`.`trx_code` = 9011) THEN 1110102002
            WHEN (`aq`.`trx_code` = 9014) THEN 1110402109
            WHEN (`aq`.`trx_code` = 9015) THEN 1110402103
            WHEN (`aq`.`trx_code` = 9016) THEN 1110402107
            ELSE 9999999999
        END) AS `cuenta`,
        CONCAT('Dunas Caja del ',
                DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d')) AS `comentario`,
        CONCAT(`aq`.`confirmation_no`,
                ' ',
                `aq`.`pname`,
                ' RM',
                `aq`.`room`,
                ' ',
                `aq`.`remark`,
                `aq`.`reference`) AS `glosa`,
        (CASE
            WHEN (`aq`.`amt` > 0) THEN `aq`.`amt`
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN (`aq`.`amt` < 0) THEN (`aq`.`amt` * -(1))
            ELSE 0
        END) AS `haberMonedaPrincipal`,
        '' AS `debeMonedaSecundaria`,
        '' AS `haberMonedaSecundaria`,
        '' AS `tasaCambio`,
        '' AS `codigoDeFicha`,
        '' AS `cancelarDocumento`,
        '' AS `tipoDeDocumento`,
        0 AS `numeroDeDocumento`,
        '' AS `serieDeDocumento`,
        '' AS `vencimientoDeDocto`,
        '' AS `CentroDeNegocios`,
        '' AS `Clasificador1`,
        '' AS `Clasificador2`,
        '' AS `MonedaReferencia`,
        '' AS `TasaReferencia`,
        '' AS `TipoDeMovimiento`,
        '' AS `NumeroDeMovimiento`,
        '' AS `codigoLegal`,
        '' AS `nombre`,
        '.' AS `giro`,
        '.' AS `direccion`,
        '.' AS `ciudad`,
        '' AS `rubro`,
        COALESCE(CAST(`aq`.`trx_date` AS DATE), '') AS `fecha_`
    FROM
        (`dunasdb`.`arqueo` `aq`
        LEFT JOIN `dunasdb`.`fiscales` `fi` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`))))
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003))